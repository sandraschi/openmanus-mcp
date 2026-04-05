# User Guide: OpenManus Bridge

## 1. Setup
Ensure **`OPENMANUS_ROOT`** is set in your `.env` pointing to a clone of the original OpenManus repo.

## 2. Handshake
Always verify the connection first:
-   `openmanus_bridge("status")` — Check if the server is alive.
-   `openmanus_bridge("validate")` — Check if the OpenManus path is correct and `main.py` exists.

## 3. Running Tasks
-   **Synchronous**: `openmanus_bridge("run_prompt", prompt="Task text...")` — Good for small jobs.
-   **Asynchronous**: `openmanus_bridge("run_prompt_async", prompt="...")` — Returns a **`job_id`**.
-   **Polling**: `openmanus_bridge("job_status", job_id="...")` — Check the result of a background job.

## 4. Sampling
If the broker asks for reasoning (`sampling_relay`), provides an industrial, materialist context about your host environment.
