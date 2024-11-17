import subprocess
import os
import re


def login_with_curl(username, password, login_url, redirect_url):
    login_command = f'curl -s -c cookies.txt -d "log={username}&pwd={password}&wp-submit=Log+In&redirect_to={redirect_url}" {login_url}'
    subprocess.run(login_command, shell=True)


def verify_login(admin_url):
    check_command = f'curl -s -b cookies.txt "{admin_url}"'
    result = subprocess.run(check_command, shell=True, capture_output=True, text=True)
    if "Log Out" in result.stdout:
        print("Login successful.")
        return True
    else:
        print("Login failed. Please check your credentials.")
        return False


def visit_plugin_install_page(plugin_install_url):
    visit_command = f'curl -s -b cookies.txt "{plugin_install_url}"'
    result = subprocess.run(visit_command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("Visited plugin install page successfully! File Located wp-content/upgrade")

        nonce_match = re.search(r'name="_wpnonce" value="(\w+)"', result.stdout)
        if nonce_match:
            return nonce_match.group(1)
        else:
            print("Failed to extract nonce.")
            return None
    else:
        print(f"Failed to visit plugin install page. Error: {result.stderr}")
        return None


def upload_plugin_with_curl(plugin_zip, nonce_value, plugin_upload_url):
    upload_command = f'curl -s -b cookies.txt -F "pluginzip=@{plugin_zip}" -F "_wpnonce={nonce_value}" "{plugin_upload_url}"'
    result = subprocess.run(upload_command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("Upload status: Success")
        print("Response:", result.stdout)
    else:
        print(f"Failed to upload plugin. Error: {result.stderr}")


def main():
    print("=== WordPress Plugin Uploader ===")
    base_url = input("Enter the WordPress base URL (e.g., http://wordpress-site.com): ").strip()
    username = input("Enter the admin username: ").strip()
    password = input("Enter the admin password: ").strip()
    plugin_zip = input("Enter the path to the plugin zip file: ").strip()


    if not os.path.isfile(plugin_zip):
        print(f"Error: File '{plugin_zip}' not found.")
        return


    login_url = f"{base_url}/wp-login.php"
    admin_url = f"{base_url}/wp-admin/"
    plugin_install_url = f"{base_url}/wp-admin/plugin-install.php?tab=upload"
    plugin_upload_url = f"{base_url}/wp-admin/update.php?action=upload-plugin"


    login_with_curl(username, password, login_url, plugin_install_url)
    if verify_login(admin_url):
        nonce = visit_plugin_install_page(plugin_install_url)
        if nonce:
            upload_plugin_with_curl(plugin_zip, nonce, plugin_upload_url)

if __name__ == "__main__":
    main()
