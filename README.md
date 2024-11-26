# Anonymous Message Bot 🤖💬

This project is an **anonymous message bot** that allows users to send and receive **text messages** anonymously. It enables communication between users without revealing their identity. 

## Important Note ⚠️
This bot is not fully completed yet and currently only handles text messages. It does not support sending files, music, or other types of content. If you would like to help complete the project and add more features, your contributions are welcome! 🙌

## Database Structure

The project requires a database for data storage, which consists of two main tables: `last` and `users`.

### Database: `bot`

#### 1. Table: `last`

This table is used to store the last messages sent to users.

| Field        | Type    | Description               |
|--------------|---------|---------------------------|
| `chat_id`    | INT     | The chat ID of the user    |
| `message`    | TEXT    | The message sent to the user |
| `id`         | INT     | Unique ID for the record   |

#### 2. Table: `users`

This table is used to store user information.

| Field                | Type    | Description                         |
|----------------------|---------|-------------------------------------|
| `chat_id`            | INT     | The chat ID of the user             |
| `username`           | VARCHAR | The username of the user            |
| `name`               | VARCHAR | The full name of the user           |
| `secret_key`         | VARCHAR | A secret key for user authentication |
| `list_of_block`      | TEXT    | List of blocked users              |
| `status_to`          | INT     | The user's status (used for specific purposes) |
| `id`                 | INT     | Unique ID for the record           |
| `chats`              | TEXT    | List of chats associated with the user |
| `reply_message_id`   | INT     | The ID of the replied message       |
| `list_of_freand`     | TEXT    | List of friends (includes name and secret key) |




## Requirements 🛠️

To run this project, you need to install the `telebot` library. This library is used to interact with the Telegram API.

You can install the `telebot` library by running the following command:

```bash
pip install pyTelegramBotAPI


