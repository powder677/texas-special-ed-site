import subprocess
import sys

def deploy_site():
    print("🚀 Preparing to deploy 750+ files...")
    
    # ---------------------------------------------------------
    # UNCOMMENT THE COMMAND FOR YOUR HOSTING PROVIDER
    # ---------------------------------------------------------
    
    # If using Vercel:
    # command = ["vercel", "--prod"]
    
    # If using Google Cloud Storage (gsutil rsync is incredibly fast):
    # command = ["gsutil", "-m", "rsync", "-R", "./your_html_folder", "gs://your-bucket-name"]
    
    # If using Firebase Hosting:
    command = ["firebase", "deploy", "--only", "hosting"]

    try:
        # This runs the command and streams the output to your terminal
        subprocess.run(command, check=True)
        print("✅ Deployment completely successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed. The command returned an error code: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: Deployment tool not found. Make sure it is installed and in your PATH.")
        sys.exit(1)

if __name__ == "__main__":
    deploy_site()