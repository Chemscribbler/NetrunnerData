# Cobra Analysis Pipeline

I discuss this notebook a bit in [this video](). Essentially using the statistics available from Cobr.ai could we get a sense of the winrate of games played with reported results. Currently IDs and 241's can be reported (though who won the 241 is not) - but for tournaments before December 2022 they likely will not have any tags for those and the fields may not exist or work.

The first part of the notebook can be modified to look at any event just by modifying the cobra url to the one of the tournament you're intersted in.

Then there is some header stuff to get faction colors (I only put colors in for Adam, sorry Sunny-stans), but should be easy to modify as needed.

# Getting it running

If you want to run this locally you'll need at miniconda or anaconda installed. I'd personally recommend just installing [miniconda](https://docs.conda.io/projects/conda/en/stable/user-guide/install/download.html#anaconda-or-miniconda) despite their recommendations to the contrary. But maybe listen to the people who made the thing and not a random schmo. When installing, if you're using an installer, I'd personally recommend adding conda to the path - even though they give you a warning about doing that. If you don't add it to the path through the installer you usually have to do it manually which is much more annoying, and the side effects they warn about likely won't cause issues that uninstall -> reinstall won't fix (and also I've never seen any...)

Once you have conda installed, open your command line tool of choice and navigate to this folder then run:

`conda env create -f env.yaml`

That will create the environment that has all the requirements for the cbi_analysis notebook. Then you'll have to select that environement called `netrunner_data` to actually run the code, though how exactly you do that will vary a bit from use to use, so I'll leave that as an excercise for the reader.