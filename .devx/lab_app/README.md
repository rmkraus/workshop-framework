# Visual Inspection Agent

<img src="_static/robots/blueprint.png" alt="VSS Robot Character" style="float:right; max-width:350px;margin:15px;" />

So far, we have focused mostly on the VSS Blueprint: its features, capabilities, and API.
We used that knowledge to create the core components for a functional system.

Now we need to integrate this new tooling with our existing processes.

## Automated Inspections and Audits

Today, we will be assiting local governments with infrastructure inspections.
Drone pilots will submit inspection footage which will then be triaged by our AI agent.

It is critical that findings from these videos get routed to the correct department.
It is also vital that safety related issues be escalated to the highest priority.

## Create your application

<img src="_static/robots/wrench.png" alt="VSS Robot Character" style="float:left; max-width:200px;margin:15px;" />

Open <a style="cursor: pointer;" onclick="openOrCreateFileInJupyterLab('labs/bridge_inspector.py');"><i class="fa-brands fa-python"></i> labs/bridge_inspector.py</a> and we can get started by checking out the initial code.

This file already has a handful of functions templated. We will work on filling these in.

At the bottom of the file is a function called `main`. This is the entry point to our application.
This funtion accepts two arguments, both of which will be defined on the command line at run time.

This function has the following structure:
  - Read in the first model id
  - **For each video file:**
    - Upload the video
    - Summarize the video
    - Chat with the video to get more detail

The reamaining functions will be called by the `main` function to accomplish this task.

### Query Model ID

Inside of the `main` function, at <a style="cursor: pointer;" onclick="goToLineAndSelect('labs/bridge_inspector.py', '# get the first model name');"># get the first model name</a>, we need to call the <a style="cursor: pointer;" onclick="goToLineAndSelect('labs/bridge_inspector.py', 'def lookup_model_id');">lookup_model_id</a> funtion. The function also needs to be populated.

Reference the previous labs to complete this function.

### Upload the video file

At this point, we will loop over all the video files specified by the user at runtime. We need to call the function
<a style="cursor: pointer;" onclick="goToLineAndSelect('labs/bridge_inspector.py', 'def upload_video_to_vss');">upload_video_to_vss</a>
function in the
<a style="cursor: pointer;" onclick="goToLineAndSelect('labs/bridge_inspector.py', '# upload the video');"># upload the video</a> block of code.

Remember this is done using a `POST` request and uploading the bytes.

### Video Summarization

<a style="cursor: pointer;" onclick="goToLineAndSelect('labs/bridge_inspector.py', 'def summarize_video');">summarize_video</a> should use the uploaded video ID to request a summary of the video. In the last excercise, we made some effective prompts that will help here.

This function should be invoked by <a style="cursor: pointer;" onclick="goToLineAndSelect('labs/bridge_inspector.py', '# summarize the video');"># summarize the video</a> block of code.

Make sure you enable chat!

### Chat with your video

Use the `Chat` class from before (it is already imported from `helpers`), and connect to the VSS Chat server. In this example, the VSS URL is provided at runtime. Put this code in the <a style="cursor: pointer;" onclick="goToLineAndSelect('labs/bridge_inspector.py', '# summarize the video');"># summarize the video</a> block.

<a style="cursor: pointer;" onclick="goToLineAndSelect('labs/bridge_inspector.py', '# ask follow up questions');"># ask follow up questions</a> should use the chat API to request additional information. We need to ask the chat model about maintenance escalations, priority of repairs, a report title, and a list of any emergency repairs that are needed.

We haven't made prompts for this yet, but try it out yourself.

<details>
<summary><b>💢 Stuck?</b></summary>

```python
escalations = chat_client.query("List any necessary escelations for maintenance.")
priority = chat_client.query("Score the priority of this report.")
title = chat_client.query("Create a title for this report.")
emergencies = chat_client.query("Does this the bridge require immediate structural attention?")
```

</details>

## Testing you application

To test your application, open a Terminal in Jupyter and navigate to `labs/`.

```bash
cd labs
```

Run your application from the command line:

```bash
./bridge_inspector.py assets/bridge.mp4
```

If everything goes to plan, this will write a full markdown report to the shell.

## 🦾 Congratulations on your new agent

<img src="_static/robots/tpose.png" alt="VSS Robot Character" style="float:right; max-width:350px;margin:15px;" />

You now have a fully fleged Video Search and Summarization agent from the NVIDIA AI Blueprint. This can be further integrated into your bussiness processes to unlock domain knowledge from video.