import pandas as pd
from sqlalchemy import create_engine

file_path = "./Demo.csv"  
df = pd.read_csv(file_path)

DATABASE_URL = "mysql+pymysql://root:1742424139@localhost/Project_demo"
engine = create_engine(DATABASE_URL)
df.to_sql("Demo", con=engine, if_exists="replace", index=False)

