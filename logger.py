# log_config.py

import logging
import os

# ========== 🔧 Logger Setup ==========
logger = logging.getLogger("username")
logger.setLevel(logging.DEBUG)

# ========== 🎨 Formatter ==========
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ========== 🗃️ File Handler ==========
log_file = "user_manager.log"
fh = logging.FileHandler(log_file)
fh.setFormatter(formatter)
logger.addHandler(fh)

# ========== 🖥️ Optional Stream Handler (Uncomment to enable terminal logs) ==========
# ch = logging.StreamHandler()
# ch.setFormatter(formatter)
# logger.addHandler(ch)


"""
📚 === EMOJI LOGGER CHEAT SHEET ===

🔥 Basic Logging Levels with Emojis

| Level         | Emoji(s)                              | Vibe / Usage                                      |
|---------------|----------------------------------------|---------------------------------------------------|
| DEBUG         | 🐛 🔍 🧠 🛠️                          | Dev insights, bug hunting, internal values        |
| INFO          | ℹ️ ✅ 📘 🧾 🪄                         | Normal ops, tracking flow                         |
| SUCCESS       | ✅ 🎉 🟢 🚀 💯                         | Task done, ops success                            |
| WARNING       | ⚠️ 🟡 👀 🚧 🫣                         | Something fishy, not broken yet                   |
| ERROR         | ❌ 🔴 🛑 💥 🤬                         | Something failed, needs fix                       |
| CRITICAL      | 💣 🚨 🔥 😱 💀                        | System down, emergency!                         

🔮 Context-Specific Emojis

| Context             | Emoji(s)                        |
|---------------------|---------------------------------|
| API Call            | 🌐 📡 📲                        |
| Database            | 🗄️ 💾 📦                        |
| Authentication      | 🔐 🧑‍💻 🪪                      |
| File System         | 📁 📝 📂                        |
| Time/Delay          | ⏳ ⏰ 🕒                        |
| Start/Init          | 🟢 🚀 🛫                        |
| Shutdown/Exit       | 🔚 🛑 👋                        |
| Network/Proxy       | 🌍 🕸️ 🧱                       |
| Retry/Loop          | 🔁 ♻️ 🔄                       |

🧪 Example Usage

    logger.debug("🐛 Debugging the user flow")
    logger.info("ℹ️ App initialized")
    logger.warning("⚠️ Disk space low")
    logger.error("❌ Couldn't connect to DB")
    logger.critical("💀 Kernel panic. Goodbye.")
"""
