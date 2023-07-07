# Instagram-Astronomy-Bot

A bot that posts astronomy pictures from NASA's API to Instagram.

## Prerequisites

- Python 3.11 (previous versions may work but are untested)

- [Pipenv](https://docs.pipenv.org/en/latest/)

- [NASA API key](https://api.nasa.gov/index.html#apply-for-an-api-key):
  fill out the form and you will receive an email with your API key

- [Instagram API key](https://developers.facebook.com/docs/instagram-api/)
  : the process is a bit more complicated, but you can follow [this tutorial](<[Title](https://levelup.gitconnected.com/automating-instagram-posts-with-python-and-instagram-graph-api-374f084b9f2b)>) to get your Instagram ID and Access Token

## How to use

1. Clone the repository
2. Install the requirements
3. Create a .env file with the following variables:

```
INSTAGRAM_ID=your_instagram_id
INSTAGRAM_ACCESS_TOKEN="your_instagram_access_token"
NASA_API_KEY="your_nasa_api_key"
```

4. Run the script

```
pipenv run python main.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ToDo

1. Messaging feature where users can send a message in date format and the bot will send them the image from that date (birthday, anniversary, etc.)
2. Mars Rover images posting

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

```

```
