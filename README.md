# WDPS Assignment -- Group 19

## Run the Code

1. Create a container by using our script `./run_container.sh`. This script creates a container, copies the code, and downloads the required spaCy model.

2. Copy the test question you want to ask into the `input_and_output` folder. (like the `example_input.txt`)

3. Run the inference using: `docker exec -it wdps-group-19 python3 /home/user/code/run_task1.py --path=/home/user/input_and_output/[example-filename]`. The first time you run the code, it will download some required models. We also provide an argument `--prompt` (default is `False`). If you set `--prompt=True`, it will use our predefined prompt, which sometimes improves the LLM model output (sometimes not).

4. The output of task 1 will be in the `input_and_output` folder as `output.txt`.

