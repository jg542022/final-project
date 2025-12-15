# final-project

Stock market app with a way to spend your money

#### How to setup database:

Go to [the dataset](https://www.kaggle.com/datasets/jacksoncrow/stock-market-dataset/data?select=symbols_valid_meta.csv) and download the zip file. Unzip it into this directory.


make sure you have installed
`pandas, mysqlconnector, and tkinter`

```
python3 main.py (creates database)
[Quit]
python3 importData.py (imports all stock market data)
```

(Importing data takes a really long time.
I had to leave my computer on overnight,
but you can stop it at any time and just
not have every stock on earth in there)

```
python3 createStoreData.py (adds items to stores)
```

Now you can run `main.py`

Create an account with your username/name in the first box and your age in the second box and click `[register]`. From now on you can just log in with your username.

You now can play the stock market by purchasing stocks and selling them. Go to the next day to see a change in your portfolio. All stocks have accurate data, so if your stock doesn't change, that's coming from the data.

Spend the money you make (or lose) on things in the shop, and view the things you've purchased in your inventory.
