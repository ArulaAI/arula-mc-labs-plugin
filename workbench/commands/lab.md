---
name: lab
description: "Start a lab session. Usage: /lab [lab_number]"
---
1. Read .claude/lab.json to determine the lab number, title, and rubric path.
2. If lab.json does not exist, prompt the user for the lab number and create a starter lab.json.
3. Start journey recording with /journey start.
4. Print the lab objectives from the rubric so the learner knows what to achieve.
