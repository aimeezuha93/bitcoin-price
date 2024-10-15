# bitcoin-price
Konfio code challenge

### Assumptions:

Before explaining the process flow, I will mention some assumptions that exist to make the process flow work.

1. The analysis will be historical, that is to say, the necessary data will be loaded in batch mode.
2. The objects in the database are created by a third party tool.
3. Sensitive data is stored outside the process.
4. The required data visualization is basic.

### Proposed solution
---

#### Stack:


* Programming language: Python(Pandas)
* Orchestrator: Apache Airflow
* Visualization tool: Metabase

As you can see, I have chosen open source tools, not because I prefer them over cloud or paid tools, I simply chose them because the setup was easier for me.

#### Worflow

1. The process checks if the CoinGecko API is available, in case it is, it continues to the next task, otherwise, it raises an AirflowFailException and terminates the process.
2. The necessary database objects are created in case they do not exist (schema and tables).
3. A query is made to the coins/list endpoint to obtain the information of all currencies and in if the currency is Bitcoin, we obtain its ID and return it.
4. We obtain the id to query from the previous task and send it to the endpoint coins/id/market_chart/range to get the historical chart data of the coin within certain time range.
5. The results are stored in a Pandas Dataframe with two columns: date and price. They are stored in the DB in the quarter_prices table. This Dataframe is saved in a temporary path within Airflow and the path where it was saved is returned.
6. We read the dataframe from the temporary file created in the previous task and calculate the 5-day moving average, save the new dataframe in the DB in the moving_average table.
7. We delete temporary files inside Airflow.

#### Installation

1. Clone the repository:
```
git clone <url>
```

2. Position yourself in the project folder at the root level.
```
cd <my_path>/bitcoin-price
```

3. Make sure you have Docker installed on your computer, if not, you can install it from here: https://docs.docker.com/engine/install/

4. Let's build the project's image. Run the following Docker command. 
```
docker-compose -f docker-compose.yml up --build
```
What this command does is to download and generate the necessary images and dependencies. 

5. We ensure that the following images have been created and are up and running with the following Docker command.
```
docker ps
```

We should see something similar to the following:

![Alt text](/images/docker_ps.png)


> [!NOTE]  
> Many times the Airflow webserver container does not start and all the others do, if this happens run in another terminal at the same root level the following Docker command.
```
docker container start <container_id>
```

6. To stop the project.
```
docker-compose stop
```

#### Other useful Airflow commands 

* Enter airflow container
```
docker exec -it {container_id} /bin/bash
```

In the airflow container:
* List Dags
```
airflow dags list
```
* Test dag
```
airflow dags test {dag_id} {execution_date_or_run_id, ex: 2022-01-01}
```
* List dag tasks
```
airflow tasks list {dag_id}
```
* Test dag task
```
airflow dags test {dag_id} {task_id} {execution_date_or_run_id, ex: 2022-01-01}
```

#### Credentials

Airflow:

- User: admin
- Pass: admin

Postgres:

- host: bitcoin-price-postgres-1,
- user: airflow,
- password: airflow,
- database: airflow,
- port: 5432

Metabase: No credentials are required, it will ask you to configure it from scratch.


### Visualization
---

As mentioned, I will use the Metabase tool to plot the moving_average table.

Metabase is easy to use for users who do not have a great expertise in data visualization and the open source version is more than enough to have visualizations that do not require great analysis and more specific visualizations.

![Alt text](/images/metabase.png)

### Scalability Plan
---

Before talking about NTR, we must take into account the following:
* The API takes approximately 1 minute to update the information of each currency(depending on the endpoint).
* The ETL processing time (in most cases 1 minute depending on the volume of information given by the API).
That gives us approximately 2 minutes of “delay”.
That said, having only this delay will depend mainly on having a listener that is always ready to send the request to the API.

It is worth mentioning that Airflow is only an orchestrator, as such it is prepared to perform processes with an indicated scheduler, it is not like some streaming tool that is always waiting to receive something, but we can make a workaround.

To the solution I propose I would add 2 things, an HTTP sensor and Spark.

1. HTTP sensor: Airflow has its own objects called operator that are nothing more than predefined functions that perform an activity, in the case of the sensors, they are operators that wait for a signal to execute the next task, in this case the signal will be that there are already updated data for all the currencies. If so, it will go to the next task, which will be the same as the current process, otherwise, it will be put on “standby” and will check every so often for new data.

2. Spark: Although the main pillar for an NRT process is the speed at which the source data is obtained, another important point is the speed at which the data is cleaned and transformed, for which Spark can efficiently handle large volumes of data streams by distributing the workload across multiple nodes.

Other tools that could be an option to Airflow:

* Apache Kafka: Stream processing tool, it has its own connectors that are always listening for new data from the source, apparently there are no connectors for HTTP requests so a custom one would have to be made which would take time.
* Apache Flink: Stream processing tool
* Amazon Kinesis.

### Data Analysis:
---