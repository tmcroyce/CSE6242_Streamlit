# CSE6242_team210
Group project for Data and Visual Analytics, team 210

# github workflow
Credit: Eva Ball (github.com/xevaballx)

Note: This doc is based on using the command line (terminal), not the VSCode extension for git.

### 0 Clone the repo
Go to GitHub in your browser. Go to our team repo and clone the project.
Click the green “code” button and clone the repo however you like. 
Copy the link.
On the command line type:
`git clone <paste link>`

### 0.1 Get your bearings
cd into the folder created by cloning, then type:
`ls` to see all the files

### 1 Ensure you are on the main Branch
`git checkout main`

### 2 Pull any new changes from dev Branch
Ensure you have the most up-to-date code
`git pull`

### 3 Create your branch
`git branch <YourFeatureHere>`
example: `git branch DogDoorActivator`

### 4 Checkout your branch
`git checkout <YourFeatureHere>`
example: `git checkout DogDoorActivator`

### 4.1 Make sure you are where you want to be
You can always type:
`git branch` to make sure you are on the branch you want to be on

### 5 Set the remote as upstream so you can eventually push changes to GitHub
`git push --set-upstream origin DogDoorActivator`

### 6 Write your code on this branch.

### 7 “Commit early push often.”
We want to push our commits to the GitHub remote feature branch often. When you are done for the day or want to take a break, commit and push.
From the root of the project folder do all three of the following:
1. `git add .` this tracks all of the files in this directory and its subdirectories
2. `git status` checks to make sure you're not committing anything you don't mean to. If you are, `git reset`, add the file you don't want to commit to .gitignore, and go back to step 1
3. `git commit -m “<YourCommitMessageHere>” `
4. `git push` this pushes any unsynced commits to remote branch on gitHub

### 7.1 Document/Comment and Test
Comment and test your code before you ask for a PR so the reviewer will have an easier time.

### 8 Pull Request (PR)
When you are completely done with your feature and you are ready to merge these changes to main, go to the GitHub repo and open a Pull Request (PR) from your branch to Main.

### 9 Ask one of your peers to review. 
If the peer has changes for you, do those changes on your branch. If it is perfect, they can merge it for you or approve it for you to merge. Click ‘squash and merge’ on the PR.

### 10 Delete your upstream branch on gitHub.
1. `git branch -d DogDoorActivator`
2. `git push origin --delete DogDoorActivator`

Or depending on your workflow, you can keep using your branch.

### 11 Repeat for your next feature! 
Starting at step 1.

# Music Similarity Visualization

## Data Files Setup

This application requires several large data files that are not included in the GitHub repository due to size limitations. Instead, these files are downloaded from Google Drive at runtime. Follow these steps to set up the data files:

1. **Upload large data files to Google Drive**:
   - Upload the following files to your Google Drive:
     - `non_nest_PCA.pkl`
     - `pitches_PCA.pkl`
     - `relevant_artist_columns.pkl`
     - `timbres_PCA.pkl`

2. **Get the file IDs from Google Drive**:
   - For each file, get the sharing link
   - Extract the ID from the URL (it's the long string after `/d/` and before any parameters)
   - Example: `https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing`
     The ID is `1a2b3c4d5e6f7g8h9i0j`

3. **Update the file IDs in the code**:
   - Open `scripts/download_helpers.py`
   - Replace `YOUR_FILE_ID_HERE` with the actual file IDs from your Google Drive

4. **Test the download script**:
   - Run `python download_data.py` to test downloading the files

## Deployment

1. Ensure all data files are properly set up with Google Drive
2. Push to GitHub
3. Deploy on Streamlit Cloud

## Running the App Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Download data files (first time only)
python download_data.py

# Run the Streamlit app
streamlit run streamlit_app.py
```
