import os
import re

# Fix resume_agent.py
f = "app/agents/resume_agent.py"
content = open(f, "r", encoding="utf-8").read()
content = content.replace(
    'logger.info(\n            "[ResumeAgent] Done. Candidate: %s | Skills: %d | Experience entries: %d",\n            result.candidate_name,',
    'logger.info(\n            "[ResumeAgent] Done. Skills: %d | Experience entries: %d",\n'
)
# Make sure to remove the third format param and format string:
content = re.sub(
    r'logger\.info\(\s*"\[ResumeAgent\] Done. Candidate: %s \| Skills: %d \| Experience entries: %d",\s*result\.candidate_name,\s*len\(result\.technical_skills\),\s*len\(result\.experience\),?\s*\)',
    r'logger.info("[ResumeAgent] Done. Skills: %d | Experience entries: %d", len(result.technical_skills), len(result.experience))',
    content
)
open(f, "w", encoding="utf-8").write(content)

# Fix interview_service.py
f = "app/services/interview_service.py"
content = open(f, "r", encoding="utf-8").read()
content = re.sub(
    r'logger\.info\("Evaluating interview answer for question: %s", request\.question\)',
    'logger.info("Evaluating interview answer.")',
    content
)
open(f, "w", encoding="utf-8").write(content)

# Fix main.py for ContextVar JSON logging
f = "app/main.py"
content = open(f, "r", encoding="utf-8").read()
# Replace basicConfig
new_logging = """
import json
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="system")

class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

settings = get_settings()

logger = logging.getLogger()
logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonLogFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z"))
logger.handlers = [handler]

logger = logging.getLogger(__name__)
"""
content = re.sub(
    r'settings = get_settings\(\)\n\nlogging\.basicConfig\([\s\S]*?logger = logging\.getLogger\(__name__\)',
    new_logging.strip(),
    content
)

# Update RequestIdMiddleware to set contextvar
new_middleware = """
            req_id = str(uuid.uuid4())
            token = request_id_var.set(req_id)
            try:
                scope["state"] = getattr(scope.get("state"), "__dict__", {})
                scope.setdefault("extensions", {})["request_id"] = req_id
                
                async def send_with_header(message):
                    if message["type"] == "http.response.start":
                        headers = dict(message.get("headers", []))
                        headers[b"x-request-id"] = req_id.encode()
                        message = {**message, "headers": list(headers.items())}
                    await send(message)

                await self.app(scope, receive, send_with_header)
            finally:
                request_id_var.reset(token)
"""
content = re.sub(
    r'req_id = str\(uuid\.uuid4\(\)\)\n\s*scope\["state"\].*?await self\.app\(scope, receive, send_with_header\)',
    new_middleware.strip(),
    content,
    flags=re.DOTALL
)

open(f, "w", encoding="utf-8").write(content)
print("Done PII logging fixes")
