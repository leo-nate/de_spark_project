from pyspark.sql.functions import *
from pyspark.sql.window import Window
from resources.dev import config
from src.main.write.database_write import DatabaseWriter
from src.main.utility.logging_config import *

#calculation for customer mart
#find out the customer total purchase every month
#write the data into MySQL table
def customer_mart_calculation_table_write(final_customer_data_mart_df):
    window = Window.partitionBy("customer_id","sales_date_month")
    final_customer_data_mart = final_customer_data_mart_df.withColumn("sales_date_month",
                                           substring(col("sales_date"),1,7).cast("date"))\
                    .withColumn("total_sales_every_month_by_each_customer",
                                sum("total_cost").over(window))\
                    .select("customer_id", concat(col("first_name"),lit(" "),col("last_name"))
                            .alias("full_name"),"address","phone_number",
                            "sales_date_month",
                            col("total_sales_every_month_by_each_customer").alias("total_sales"))\
                    .distinct()

    final_customer_data_mart.show()

    logger.info("************ Write customer sales data to postgres")
    #Write the Data into Postgres customers_data_mart table
    db_writer = DatabaseWriter(url=config.url,properties=config.properties)
    db_writer.write_dataframe(final_customer_data_mart,config.customer_data_mart_table)

