#----------------------------------------------------------------
# SQL Preprocessing Pipeline Titanic Classification Example
# Postgres based examples - https://www.postgresql.org/
# Setup is described in README.md
#----------------------------------------------------------------

#append system path to import cousin packages
import sys

from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
sys.path.append("/Users/weisun/Coding Projects/Machine Learning/SQLDATAPREP4ML")

from sql_preprocessing import *
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.compose import *
from sklearn.preprocessing import *
from sklearn.pipeline import *
from sklearn.model_selection import train_test_split

# Fix LabelEncoder
class LabelEncoder2(LabelEncoder):
    def fit(self, X, y=None):
        super(LabelEncoder2, self).fit(X)
    def transform(self, X, y=None):
        res = super(LabelEncoder2, self).transform(X)
        df = pd.DataFrame(data=res)
        return df
    def fit_transform(self, X, y=None):
        return super(LabelEncoder2, self).fit(X).transform(X)

# Postgress connection
# User: postgress, password: password
dbconn = SqlConnection("postgresql://weisun:password@localhost:5432/db1", print_sql=True)


# Database functions
#----------------------------------------------------------------

csv_file = "titanic_dataset.csv"
sdf_name = 'titanic'
dataset_schema = 's1'
dataset_table = 'titanic'
key_column = 'key_column'
catalog_schema = dataset_schema
fit_schema = dataset_schema
default_order_by = None
db_args = {}

# load csv and store it to db (if does not exist yet)
df = pd.read_csv(csv_file)

# create SqlDataFrame pointing to table s1.sd_1 (loaded above)
sdf = dbconn.get_sdf_for_table(sdf_name, dataset_schema, dataset_table, key_column, fit_schema, default_order_by, **db_args)


#split the dataset - to training and test
#x_train, x_test, y_target_train, y_target_test = cross_validation.train_test_split(tmp_x, tmp_y, test_size=0.25, random_state=0)
x_train_sdf1, x_test_sdf1, y_train_df1, y_test_df1 = sdf.train_test_split(test_size=0.25, random_state=0, y_column='Survived')

x_df = df.drop('Survived', axis=1)
y_df = df['Survived']
x_train_df2, x_test_df2, y_train_df2, y_test_df2 = train_test_split(x_df, y_df,test_size=0.25, random_state=0)

preprocessor_db = SqlColumnTransformer(
    transformers=[
        ('age', SqlSimpleImputer(strategy='mean'), 'age'),
        ('pclass', SqlOneHotEncoder(), 'pclass'),
        ('sex', SqlLabelEncoder(), 'sex')
    ]
)

preprocessor_df = ColumnTransformer(
    transformers=[
        ('Age', SimpleImputer(strategy='mean'), ['Age']),
        ('Pclass', OneHotEncoder(), ['Pclass']),
        ('Sex', LabelEncoder2(), ['Sex'])
    ]
)

pipeline_db = SqlPipeline(steps=[
    ('preprocessor', preprocessor_db),
    ('classifier', DecisionTreeClassifier())
    ])

print(pipeline_db)

pipeline_df = Pipeline(steps=[
    ('imputer', preprocessor_df),
    ('classifier', DecisionTreeClassifier())
    ])

print(pipeline_df)

pipeline_db.fit(x_train_sdf1, y_train_df1)

print("Sql preprocessing model score: %.3f" % pipeline_db.score(x_test_sdf1, y_test_df1))

pipeline_df.fit(x_train_df2, y_train_df2)

print("sklearn preprocessing model score: %.3f" % pipeline_df.score(x_test_df2, y_test_df2))