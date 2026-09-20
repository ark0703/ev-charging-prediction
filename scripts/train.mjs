import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const isWindows = process.platform === "win32";
const python = isWindows ? "python" : "python3";
const venvDir = path.join(root, ".venv");

function run(command, args) {
  const result = spawnSync(command, args, {
    cwd: root,
    stdio: "inherit",
    shell: isWindows,
  });

  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}

if (!existsSync(venvDir)) {
  run(python, ["-m", "venv", ".venv"]);
}

run(python, ["-m", "pip", "install", "-r", "requirements.txt"]);
run(python, ["ml/generate_data.py"]);
run(python, ["ml/train.py"]);

console.log("Training complete. Artifacts saved to models/");
