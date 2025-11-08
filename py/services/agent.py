from tasks import create_task, update_task
from executor import execute
import ollama

def run_agent(goal: str, max_steps: int = 5) -> list:
    steps = []
    current = goal

    for i in range(max_steps):
        response = execute(current)
        steps.append({ "step": i + 1, "input": current, "output": response })

        feedback = ollama.chat(
            model="llama3",
            messages=[
                { "role": "system", "content": "Evaluate the last output and decide the next step toward the goal." },
                { "role": "user", "content": f"Goal: {goal}\nLast output: {response}" }
            ]
        )

        next_step = feedback["message"]["content"].strip()
        if next_step.lower() in ["done", "complete", "no further steps"]:
            break

        current = next_step

    create_task(goal, steps)
    return steps