import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modelPath = path.join(root, "models", "model.joblib");

if (existsSync(modelPath)) {
  process.exit(0);
}

console.log("Model not found. Running training pipeline...");
const isWindows = process.platform === "win32";
const python = isWindows ? "python" : "python3";

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

run(python, ["ml/generate_data.py"]);
run(python, ["ml/train.py"]);
