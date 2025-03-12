# RapidPrompt

RapidPrompt is a PyQt5-based UI tool that demonstrates an advanced, multi-panel interface with customizable text fields, editable headers, and an elegant dark/light mode toggle. Designed as a proof-of-concept, this “gross product” showcases custom widget techniques such as rounded outline frames, a custom toggle switch, and dynamic splitter layouts.

## Features

- **Three-Panel Layout:**
  - **Part 1:** A multi-line text input field.
  - **Part 2:** A read-only display that updates with the input from Part 1.
  - **Part 3:** A dynamic list of multi-line text fields with editable headers.
- **Custom Outline Frames:**  
  Each panel is wrapped in a rounded outline with consistent styling. The outlines have been carefully designed to leave space for splitter handles and always maintain padding between the border and content.
- **Dark/Light Mode Toggle:**  
  Easily switch between dark and light themes. Both the main UI and the settings overlay animate their background colors in sync.
- **Responsive Settings Overlay:**  
  A settings panel lets you reset the layout, toggle themes, and adjust the number of text fields in Part 3.
- **Elegant Styling:**  
  All text fields share a consistent look with elegant rounded edges, matching outer borders, and background colors that stand out appropriately based on the current theme.

## Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/yourusername/rapidprompt.git
   ```

2. Navigate to the project directory:

    ```
    cd rapidprompt
    ```

3. (Optional) Create and activate a virtual environment:

    ```
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate'
    ```

4. Install the required dependencies:

    ```
    pip install -r requirements.txt
    ```


## Usage

Run the application with:

    ```
    python main.py
    ```



## Project Structure

 - main.py:
    The entry point of the application.
 - ui.py:
    Contains the complete PyQt5 UI implementation including all custom widgets and styling.
 - requirements.txt:
    Lists all dependencies.

## Contributing

Contributions, suggestions, and bug reports are welcome! Feel free to open issues or submit pull requests to improve the project.

## License

This project is licensed under the MIT License.

## Disclaimer

RapidPrompt is a prototype developed to showcase custom PyQt5 interface techniques. It is provided "as is" without any warranty. Use it as a starting point for your own projects or as inspiration for custom UI development.