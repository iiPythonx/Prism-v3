## Prism v3 - the final version
---

![](https://img.shields.io/github/commit-activity/m/ii-Python/Prism-v3) ![](https://img.shields.io/github/languages/code-size/ii-Python/Prism-v3) ![](https://img.shields.io/tokei/lines/github/ii-Python/Prism-v3)

Welcome to the Prism v3 repository, hosting the code for Prism v3.  
Prism is a self-hosted bot, but it also has a public instance hosted by me ([invite](https://discord.com/api/oauth2/authorize?client_id=862456523209179147&permissions=2147609664&scope=applications.commands%20bot)).

---

### 🧰 Setup

Before you start the setup process, you need to install the needed requirements.  
Please note these commands may change depending on your environment.

You require the following (before being able to continue at all):
- Python 3.9+ (**latest is recommended**); download it from [python.org](https://python.org)
- Git; download it from [git-scm.com](https://git-scm.com)

The following script should setup the base repository:
```
git clone https://github.com/ii-Python/Prism-v3
cd Prism-v3
python3 -m pip install -r reqs.txt
mv example_config.json config.json
```

### 🔧 Configuration

Before you actually use Prism, you need to configure it.  
This process requires both a `.env` file as well as a `config.json` file.

To setup the `.env`, grab your [discord bot token](https://discord.com/developers/applications), and place it like so:
```
TOKEN = "YOUR DISCORD BOT TOKEN"
```

The `config.json` should look like the following:
```json
{
    "admin": {
        "owner": "Somebody#0001",
    },
    "prefix": {
        "value": "p!",
        "allow_change": true
    },
    "paths": {
        "db_dir": "db",
        "cmd_path": "prism/cmds"
    },
    "status": {
        "watching": ["Twitch.tv"],
        "playing": ["Minecraft"],
        "enabled": true
    }
}
```

The following are required:
- `admin/owner`, which is used in the help command (among other places)
- `prefix/value`, which is the bot prefix
- `prefix/allow_change`, which toggles whether users can change their server prefixes or not
- `paths/db_dir`, the database folder location
- `paths/cmd_path`, the command folder location

The rest of the options are up to you to tweak on your own accord.  
Launching the bot is as simple as running `python3 launch.py`

For more configuration, please consult the [wiki](https://github.com/ii-Python/Prism-v3/wiki).

---

### 👥 Credits

| iiPython    | DmmD        | Emy          |
| ----------- | ----------- | ------------ |
| ![iiPython](https://avatars.githubusercontent.com/u/35084023?v=4&size=60) | ![Dm123321_31mD](https://media.discordapp.net/attachments/687043700169244763/897972274433515540/Dm123321_31mD_Round.png?width=60&height=60) | ![Emy](https://avatars.githubusercontent.com/u/69433142?v=4&size=60)


### 📝 License

Prism is listed under the MIT license, more information [here](https://opensource.org/licenses/MIT).  
LICENSE.txt contains the raw license.
