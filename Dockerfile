# Use Python 3.8.20 as the base image
FROM python:3.8.20-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt to the container
COPY requirements.txt .

# Install Rust and Cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
RUN source $HOME/.cargo/env


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app’s code into the container
COPY . .

# Expose port 8501 for Streamlit
EXPOSE 8501

# Command to run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
