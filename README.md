# 📋 Dropboard

**Made with 💜 for HackClub**

A real-time social media web app designed for teenagers to anonymously share confessions and secrets. Users can post anonymously with a title, description, and optional poll. Others can beowse and upvote posts, and engage with other teens with features like live chat, live whiteboards to express how they feel with colour, and interactive polls powered by sockets.

## ✨ Features

### **100% Anonymous**
- No accounts, no emails, no tracking
- Pure anonymous sharing with content moderation
- Safe space for teens to express themselves

### **Real-Time Interactive Features**
- **Live Chat**: Real-time messaging with colored usernames
- **Collaborative Whiteboard**: Draw colored clouds together in real-time
- **Live Polls**: Create and vote on polls with instant results
- **WebSocket Integration**: All interactions happen instantly across all connected users

### **Core Functionality**
- **Anonymous Posts**: Share confessions with titles and content
- **Upvoting System**: Support posts that resonate with you
- **Comment System**: Provide anonymous support and advice
- **Content Moderation**: Automatic filtering for inappropriate content
- **Country-Based Sharing**: See where posts are coming from

## Tech Stack

- **Backend**: Python Flask with Flask-SocketIO
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Real-Time**: WebSocket connections via Socket.IO
- **Database**: Firebase Realtime Database
- **Styling**: Custom neon color palette with handwriting fonts
- **Deployment**: Ready for cloud deployment

## Real-Time Features

### Live Whiteboard
- Collaborative drawing with 6 neon colors
- Real-time line synchronization across all users
- Full-screen mode for immersive experience
- Touch-friendly interface

### Live Chat
- Instant message broadcasting
- Persistent chat history
- Colored usernames for easy identification
- Character limits and moderation

### Interactive Polls
- Create custom polls with multiple options
- Real-time vote counting and visualization
- Progress bars showing vote distribution
- One vote per user per poll

## How It Works

1. **Write**: Share your secret with a title and context
2. **Stay Safe**: Our filters keep things respectful
3. **Get Support**: Others can comment and upvote anonymously
4. **Connect**: Join live sessions to chat and draw together

## 🔧 Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dropboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Firebase**
   - Set up a Firebase Realtime Database
   - Update `config.txt` with your Firebase URL
   - Add your Firebase service credentials to `service.json`

4. **Run the application**
   ```bash
   python main.py
   ```

## HackClub Project #hackmate

This project was created as part of the HackClub #hackmate **ysws**, demonstrating:
- **Real-time web development** with WebSockets
- **Anonymous social platforms** with proper moderation
- **Modern UI/UX design** for teen audiences
- **Full-stack development** with Python and JavaScript
- **Database integration** with Firebase

## Contributing

This is a HackClub project! Feel free to:
- Add new real-time features
- Improve the UI/UX design
- Enhance content moderation
- Add new interactive elements

## License

Created for educational purposes and the HackClub community.

---

**Made with 💜 for teens who need a safe space to share**

*Created by [Jim](https://github.com/jimmydin7/)* 
