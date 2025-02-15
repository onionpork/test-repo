import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    
    INPUTS:
        messages_filepath - the filepath where the messages.csv is located
        categories_filepath - the filepath where the categories.csv is located
    RETURNS:
        df - the dataframe mergeing both the message and categories 
                csv files
    """
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    df = pd.merge(messages, categories, left_on='id', right_on='id')
    return df

def clean_data(df):
    """
    INPUTS:
        df - the disaster message dataframe
    RETURNS:
        df - the cleaned disaster message dataframe
    """
    categories = df.categories.str.split(";", expand=True)
    row = categories.iloc[0]
    category_colnames = list(row.str.split('-').apply(lambda x: x[0]))
    categories.columns = category_colnames
    categories.related.loc[categories.related == 'related-2'] = 'related-1'
    
    for column in categories:
        categories[column] = categories[column].str.split('-').apply(lambda x: x[1])
        categories[column] = categories[column].astype('int64')
        
    df = pd.concat([df.drop('categories', axis=1), categories], axis =1)
    df = df.drop_duplicates()
    assert len(df[df.duplicated()]) == 0
    return df

def save_data(df, database_filename):
    """
    Save disaster message df into a SQLite database.
    
    INPUTS:
        df - the disaster message df
        database_filename - the filepath to store the disaster message SQLite database
    """
    engine = create_engine('sqlite:///'+database_filename)
    conn = engine.connect()
    df.to_sql('disaster_cat', engine, index=False, if_exists = 'replace')
    conn.close()
    engine.dispose()

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()