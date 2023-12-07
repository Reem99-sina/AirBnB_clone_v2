#!/usr/bin/python3
"""
Fabric script that deletes out-of-date archives
"""

from fabric.api import env, local, run
from fabric.operations import put
from datetime import datetime
import os

# Servers
env.hosts = ['<IP web-01>', '<IP web-02>']

# Archive format
archive_format = "web_static_{}.tgz"


def do_pack():
    """
    Create a compressed archive of the web_static folder.

    Returns:
        str: Archive path if successful, None otherwise.
    """
    try:
        # Create a unique archive file name based on the current date and time
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        archive_name = archive_format.format(timestamp)

        # Create the compressed tar archive
        local(f"tar -czvf {archive_name} web_static")

        # Return the archive path if successful
        return archive_name

    except Exception as e:
        # Print the exception (you may want to handle it differently)
        print(f"Error: {e}")

        # Return None if the archive generation fails
        return None


def do_deploy(archive_path):
    """
    Deploy the archive to the web servers.

    Args:
        archive_path (str): Local path to the archive.
    """
    if not os.path.exists(archive_path):
        return False

    try:
        # Upload the archive to the server
        put(archive_path, '/tmp/')

        # Extract the archive to the web servers
        archive_name = os.path.basename(archive_path).split('.')[0]
        remote_path = f'/data/web_static/releases/{archive_name}/'
        run(f'mkdir -p {remote_path}')
        run(f'tar -xzf /tmp/{archive_name}.tgz -C {remote_path}')
        run(f'rm /tmp/{archive_name}.tgz')

        # Create a symbolic link
        current_link = '/data/web_static/current'
        run(f'rm -f {current_link}')
        run(f'ln -s {remote_path} {current_link}')

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def do_clean(number=0):
    """
    Delete out-of-date archives.

    Args:
        number (int): Number of archives to keep.
    """
    try:
        number = int(number)
        if number < 0:
            return

        # Get the list of archives in the versions folder
        local_archives = local("ls -1t versions", capture=True).splitlines()

        # Delete unnecessary local archives
        for archive in local_archives[number:]:
            local(f"rm versions/{archive}")

        # Get the list of releases on the remote servers
        remote_archives = run("ls -1t /data/web_static/releases", quiet=True).splitlines()

        # Delete unnecessary remote archives on each server
        for archive in remote_archives[number:]:
            run(f"rm -rf /data/web_static/releases/{archive}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    # Example usage:
    archive_path = do_pack()
    if archive_path:
        do_deploy(archive_path)
        do_clean(2)
