import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score 

df = pd.read_csv("processed_websites2.csv")
df["combined_text"] = (
    df["url"].fillna("") + " " +
    df["domain"].fillna("") + " " +
    df["domain_tokens"].fillna("") + " " +
    df["url_keywords"].fillna("") + " " +
    df["text"].fillna("") + " " +
    df["title"].fillna("") + " " +
    df["meta_description"].fillna("")
)


vectorizer=TfidfVectorizer(stop_words='english',max_df=0.8,ngram_range=(1,1))
x=vectorizer.fit_transform(df['combined_text'])
y=df['category']
x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.1,random_state=42)

model=SVC(kernel="linear")
model.fit(x_train,y_train)

predicitions=model.predict(x_test)
score=accuracy_score(y_test,predicitions)
print(score)