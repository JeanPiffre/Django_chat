import os

def create_folder():
    private_key_dir = "privateKey"
    if not os.path.exists(private_key_dir):
        os.makedirs(private_key_dir)
        print(f"Dossier '{private_key_dir}' créé.")

    public_key_dir = "publicKey"
    if not os.path.exists(public_key_dir):
        os.makedirs(public_key_dir)
        print(f"Dossier '{public_key_dir}' créé.")

def create_files(filename):
    private_key_file = os.path.join("privateKey", f"{filename}.pem")
    if not os.path.exists(private_key_file):
        open(private_key_file, "a").close()

    public_key_file = os.path.join("publicKey", f"{filename}.pem")
    if not os.path.exists(public_key_file):
        open(public_key_file, "a").close()