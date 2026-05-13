# Rust Installation Guide

## Step 1: Install Rust

Run the official Rust installer script from the Rust website.

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Step 2: Load Cargo Environment

After installation completes, source the Cargo environment file to make the tools available in your current terminal session.

```bash
source "$HOME/.cargo/env"
```

## Step 3: Make the Path Permanent

Add the Cargo bin directory to your PATH by appending the export line to your bash configuration file. This ensures Rust and Cargo are available every time you open a new terminal.

```bash
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
```

## Step 4: Reload Shell Configuration

Source your bash configuration file to apply the changes immediately without restarting your terminal.

```bash
source ~/.bashrc
```

## Step 5: Verify Installation

Confirm that both Cargo and the Rust compiler are installed correctly by checking their versions.

```bash
cargo --version
rustc --version
```

## Step 6: Create a New Project

Once Rust is installed, you can use Cargo to create a new project. For example, create a new project called prediction-api.

```bash
cargo new prediction-api
```

## Step 7: Install rust-analyzer Extension

### VS Code

Open the Extensions panel, search for rust-analyzer, and install the extension by the Rust Programming Language group.

Or install it directly from the command line:

```bash
code --install-extension rust-lang.rust-analyzer
```

## Step 8: Create Workspace Cargo.toml

At the root of your workspace, create a file called `Cargo.toml` and add prediction-api as one of its members.

```toml
[workspace]
resolver = "3"

members = [
    "services/prediction-api"
]
```

---

## Resources

For more information and the official installer, visit the Rust website at rust-lang.org/tools/install.