import json
import os

from agent import run_agent

WORKING_DIRECTORY = "./test"
RUNS_PER_TASK = 3

tasks = []
with open("tasks.json") as f:
    tasks = json.load(f)


def cleanup(task):
    for path in task.get("cleanup", []):
        full_path = os.path.join(WORKING_DIRECTORY, path)
        if os.path.isfile(full_path):
            os.remove(full_path)


def passed(task, result):
    return result.success and task["expect"].lower() in result.answer.lower()


summary = []
for task in tasks:
    results = []
    for run in range(RUNS_PER_TASK):
        cleanup(task)
        result = run_agent(task["prompt"], max_rounds=task["max_rounds"])
        results.append(result)
    cleanup(task)

    print(f"--- {task['id']} --- \n ")
    for i, result in enumerate(results):
        print(f"{task['id']}-{i} passed: {passed(task, result)} \n {result.answer} \n ")

    pass_rate = sum(passed(task, r) for r in results) / len(results)
    avg_rounds = sum(r.rounds for r in results) / len(results)
    summary.append((task["id"], len(results), pass_rate, avg_rounds))

print(f"{'TASK':<20} {'RUNS':>4} {'PASS-RATE':>10} {'AVG-ROUNDS':>11}")
for task_id, runs, pass_rate, avg_rounds in summary:
    print(f"{task_id:<20} {runs:>4} {pass_rate:>9.0%} {avg_rounds:>11.1f}")
