from src.sqlalchemy.db import db_session

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.orm import sessionmaker
from src.sqlalchemy.models import EnhancedTransaction

# Assuming you have an engine configured to connect to your database
query = db_session.query(EnhancedTransaction)

# Convert query result to pandas DataFrame
df = pd.read_sql(query.statement, query.session.bind)

# Close the session
db_session.close()

# Plotting Histograms/Distribution Plots
plt.figure(figsize=(10, 6))
sns.histplot(df['value'], kde=True)
plt.title('Distribution of Transaction Value')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.show()

plt.figure(figsize=(10, 6))
sns.histplot(df['balance'], kde=True)
plt.title('Distribution of Balance')
plt.xlabel('Balance')
plt.ylabel('Frequency')
plt.show()

# Plotting Scatter Plot
plt.figure(figsize=(10, 6))
sns.scatterplot(x='value', y='balance', data=df)
plt.title('Scatter Plot: Value vs Balance')
plt.xlabel('Value')
plt.ylabel('Balance')
plt.show()

# Plotting Count Plots
plt.figure(figsize=(10, 6))
sns.countplot(x='type', data=df)
plt.title('Count Plot: Transaction Type')
plt.xlabel('Type')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()

plt.figure(figsize=(10, 6))
sns.countplot(x='source', data=df)
plt.title('Count Plot: Source')
plt.xlabel('Source')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.show()

# Plotting Box Plot
plt.figure(figsize=(10, 6))
sns.boxplot(x='type', y='value', data=df)
plt.title('Box Plot: Transaction Value by Type')
plt.xlabel('Type')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.show()

# Plotting Time Series Plot
plt.figure(figsize=(12, 6))
sns.lineplot(x='date', y='value', data=df)
plt.title('Time Series Plot: Transaction Value over Time')
plt.xlabel('Date')
plt.ylabel('Value')
plt.show()
