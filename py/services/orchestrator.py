from plugin_loader import route_to_plugin
from tasks import create_task
from orb import set_orb_state
import ollama

def orchestrate(goal: str, max_steps: int = 5) -> list:
    steps = []
    current = goal
    set_orb_state("thinking")

    for i in range(max_steps):
        plugin_response = route_to_plugin(current)
        if plugin_response:
            set_orb_state("executing")
            steps.append({ "step": i + 1, "input": current, "output": plugin_response })
            set_orb_state("thinking")
        else:
            response = ollama.chat(
                model="llama3",
                messages=[
                    { "role": "system", "content": "Decide the next plugin-based step to achieve this goal." },
                    { "role": "user", "content": f"Goal: {goal}\nPrevious steps: {steps}" }
                ]
            )
            next_step = response["message"]["content"].strip()
            if next_step.lower() in ["done", "complete", "no further steps"]:
                break
            current = next_step
            continue

        feedback = ollama.chat(
            model="llama3",
            messages=[
                { "role": "system", "content": "Evaluate the last plugin output and suggest the next plugin step." },
                { "role": "user", "content": f"Goal: {goal}\nLast output: {plugin_response}" }
            ]
        )
        current = feedback["message"]["content"].strip()

    create_task(goal, steps)
    set_orb_state("idle")
    return steps