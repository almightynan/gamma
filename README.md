# gamma

**gamma** is a Python-based interface for working with MySQL — designed with students in mind. Think of it like a modern, no-nonsense alternative to WampServer, minus the bloat and compatibility nightmares.

**Live Website**: [gamma.almightynan.cc](https://gamma.almightynan.cc)


## 🔍 What is gamma?

gamma offers a lightweight interface to:

- Connect to MySQL databases
- Run SQL commands via CLI
- Visualize tables and schema
- Use AI to generate SQL queries, tables, and more

It’s built to be simple, fast, and student-friendly — no more dealing with missing Visual C++ redistributables or cryptic WAMP issues on school PCs.

> This started as a quick tool for my classmates and myself when we kept running into issues with WAMP. Now it's open source.

## 🎯 Why Gamma?

- ✅ Minimal setup
- ✅ Built with Python (easy to extend)
- ✅ AI-assisted features for learning and productivity (default username is `nan`; password is `0001`)
- ✅ Compatible with Windows, Linux, and macOS
- ✅ Developed by students, for students

## 🚀 Features

- **CLI-based SQL interaction**  
  Run MySQL queries directly from the app’s built-in terminal.

- **Table visualization**  
  Easily browse and inspect your database structure and contents.

- **AI-powered tools**  
  Generate SQL queries, table schemas, and more using AI prompts.

- **Error-resistant design**  
  No more “missing DLL” issues — Gamma avoids common setup failures by not relying on bloated dependencies.

## 🛠️ Future Plans?

- Maybe adding **PHP** and **Apache** support — think WampServer, but actually good.
- Expanding the AI capabilities (explain queries, optimize performance, etc.)
- More GUI improvements and export/import features.

## 👥 Who’s it for?

- Students
- Beginners working with MySQL

## 📦 Installation

1. ```git clone https://github.com/yourusername/gamma```
2. ```cd gamma```
3. Download MySQL binaries from releases folder ([`releases > mysql5.7.40.zip`](https://github.com/AlmightyNan/gamma/releases/tag/production))
4. Extract the downloaded `.zip` file, copy the folder and paste it within `gamma` directory.
5. ```pip install -r requirements.txt```
6. ```python main.py```
   
## 📂 Project Structure

```
gamma/
├── assets/              # App resources (UI, configs, etc.)
├── classes/             # Core classes (AI features, MySQL handlers, etc.)
├── mysql5.7.40/         # Bundled MySQL binary (portable)
├── debug.log            # Logs for debugging
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
└── README.md            # You’re looking at it
```

## 🤝 Contributing

Pull requests welcome. If you’re someone who found WAMP annoying too — help make Gamma better.

## 🪪 License

```
MIT License

Copyright (c) 2025 AlmightyNan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
