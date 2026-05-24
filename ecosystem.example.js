module.exports = {
  apps: [
    {
      name: "NeuroNewsBot",
      script: "/root/NeuroNewsBot/main.py",
      cwd: "/root/NeuroNewsBot",
      interpreter: "python3",
      // Optional: interpreter_args: "-u" enforces unbuffered output so logs show up immediately
      interpreter_args: "-u",
      env: {
        TELEGRAM_BOT_TOKEN: "YOUR_TELEGRAM_BOT_TOKEN_HERE",
        TELEGRAM_CHAT_ID: "YOUR_TELEGRAM_CHAT_ID_HERE",
        GROQ_API_KEY: "YOUR_GROQ_API_KEY_HERE",
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
};
