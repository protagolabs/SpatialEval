# SpatialEval

## Setup Environments
This repository has been tested with Python version 3.10.13.

Install requirements with the command:
```
pip install -r requirements.txt
```

## Task 1. Draw some points in 2d grid

1. Synthesize data
	```
	python 2d_grid_point/2d_grid.py <n_samples> <points_in_a_grid> <grid_size>
	```
The data will be saved in `data/2d_grid_samples<n_samples>_points<points_in_a_grid>_size<grid_size>.json`.

2. Evaluate and save results  

    a. Set your OPENAI_API_KEY in `utils/chat_models.py`  

    b. Run the following command  
	```
	python 2d_grid_point/eval_2d_grid.py --path=<path_to_data> --model=<model_name>
	```  

    We can get an accuracy after the evaluation.

## Task 2. 2D Path Planning
1. Synthesize data
	```
	cd path_planning
	python path_planning/RandomObstacles.py
	```

2. Evaluate and save results  

    a. Set your OPENAI_API_KEY in `utils/chat_models.py`  

    b. Run the following command  
    ```shell
    python path_planning/get_gpt_answer.py  
    python path_planning/format_gpt4_output.py  
    python path_planning/evaluate_gpt4_answer.py  
    ```  
   We can get an accuracy after the evaluation.
