#!/usr/bin/env python3
"""
Detect the tech stack of a project by scanning config files and dependencies.

Usage:
    python detect_stack.py [project-root]
    python detect_stack.py  (defaults to current directory)

Outputs a JSON report of detected framework, database, auth, payments,
existing deploy config, and environment variables.

The agent uses this to determine which deployment steps are needed.
"""

import json
import os
import re
import sys
from pathlib import Path


def read_file_safe(path: Path) -> str:
    """Read a file, return empty string if it doesn't exist."""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return ""


def detect_package_manager(root: Path) -> str:
    """Detect which package manager the project uses."""
    if (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        return "bun"
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    if (root / "package-lock.json").exists():
        return "npm"
    return "npm"  # default


def detect_framework(root: Path, pkg: dict) -> dict:
    """Detect the web framework from package.json and config files."""
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    
    framework = {"name": "unknown", "version": None, "config_file": None}

    if "next" in deps:
        framework["name"] = "nextjs"
        framework["version"] = deps["next"]
        if (root / "next.config.js").exists():
            framework["config_file"] = "next.config.js"
        elif (root / "next.config.mjs").exists():
            framework["config_file"] = "next.config.mjs"
        elif (root / "next.config.ts").exists():
            framework["config_file"] = "next.config.ts"
    elif "astro" in deps:
        framework["name"] = "astro"
        framework["version"] = deps["astro"]
        if (root / "astro.config.mjs").exists():
            framework["config_file"] = "astro.config.mjs"
    elif "@sveltejs/kit" in deps:
        framework["name"] = "sveltekit"
        framework["version"] = deps["@sveltejs/kit"]
    elif "@remix-run/node" in deps or "@remix-run/react" in deps:
        framework["name"] = "remix"
        framework["version"] = deps.get("@remix-run/node", deps.get("@remix-run/react"))
    elif "nuxt" in deps:
        framework["name"] = "nuxt"
        framework["version"] = deps["nuxt"]
    elif "vite" in deps and "react" in deps:
        framework["name"] = "vite-react"
        framework["version"] = deps["vite"]
    elif "vite" in deps:
        framework["name"] = "vite"
        framework["version"] = deps["vite"]

    return framework


def detect_database(root: Path, pkg: dict, env_vars: list) -> dict:
    """Detect database setup from dependencies and config files."""
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    
    db = {"provider": None, "orm": None, "has_migrations": False, "config_file": None}

    # Check ORM
    if "prisma" in deps or "@prisma/client" in deps:
        db["orm"] = "prisma"
        if (root / "prisma" / "schema.prisma").exists():
            db["config_file"] = "prisma/schema.prisma"
        if (root / "prisma" / "migrations").exists():
            db["has_migrations"] = True
    elif "drizzle-orm" in deps:
        db["orm"] = "drizzle"
        if (root / "drizzle.config.ts").exists():
            db["config_file"] = "drizzle.config.ts"
        elif (root / "drizzle.config.js").exists():
            db["config_file"] = "drizzle.config.js"
        if (root / "drizzle").exists():
            db["has_migrations"] = True

    # Check provider
    if "@supabase/supabase-js" in deps:
        db["provider"] = "supabase"
        if (root / "supabase" / "config.toml").exists():
            db["config_file"] = db["config_file"] or "supabase/config.toml"
    elif "@neondatabase/serverless" in deps:
        db["provider"] = "neon"
    elif "@planetscale/database" in deps:
        db["provider"] = "planetscale"

    # Infer from env vars
    if not db["provider"]:
        for var in env_vars:
            if "SUPABASE" in var:
                db["provider"] = "supabase"
                break
            elif "NEON" in var or "DATABASE_URL" in var:
                db["provider"] = "neon-or-postgres"
                break

    return db


def detect_auth(root: Path, pkg: dict, env_vars: list) -> dict:
    """Detect authentication setup."""
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    
    auth = {"provider": None, "has_config": False}

    if "@clerk/nextjs" in deps or "@clerk/clerk-react" in deps:
        auth["provider"] = "clerk"
        auth["has_config"] = any("CLERK" in v for v in env_vars)
    elif "next-auth" in deps or "@auth/core" in deps:
        auth["provider"] = "authjs"
        config_files = ["auth.ts", "auth.js", "app/api/auth/[...nextauth]/route.ts"]
        auth["has_config"] = any((root / f).exists() for f in config_files)
    elif "lucia" in deps or "lucia-auth" in deps:
        auth["provider"] = "lucia"

    # Check if using Supabase Auth (no separate package)
    if not auth["provider"]:
        for var in env_vars:
            if "SUPABASE" in var:
                # Supabase Auth uses the same client as the database
                auth["provider"] = "supabase-auth"
                break

    return auth


def detect_payments(root: Path, pkg: dict, env_vars: list) -> dict:
    """Detect payment provider setup."""
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    
    payments = {"provider": None, "has_keys": False}

    if "stripe" in deps or "@stripe/stripe-js" in deps:
        payments["provider"] = "stripe"
        payments["has_keys"] = any("STRIPE" in v for v in env_vars)
    elif "@lemonsqueezy/lemonsqueezy.js" in deps:
        payments["provider"] = "lemonsqueezy"
        payments["has_keys"] = any("LEMON" in v for v in env_vars)

    return payments


def detect_deploy_config(root: Path) -> dict:
    """Detect existing deployment configuration."""
    config = {"provider": None, "config_file": None, "has_dockerfile": False}

    if (root / "vercel.json").exists():
        config["provider"] = "vercel"
        config["config_file"] = "vercel.json"
    elif (root / ".vercel" / "project.json").exists():
        config["provider"] = "vercel"
        config["config_file"] = ".vercel/project.json"
    elif (root / "railway.toml").exists():
        config["provider"] = "railway"
        config["config_file"] = "railway.toml"
    elif (root / "fly.toml").exists():
        config["provider"] = "fly"
        config["config_file"] = "fly.toml"
    elif (root / "render.yaml").exists():
        config["provider"] = "render"
        config["config_file"] = "render.yaml"

    config["has_dockerfile"] = (root / "Dockerfile").exists()

    return config


def collect_env_vars(root: Path) -> dict:
    """Collect environment variables from env files and code references."""
    env_files = {}
    code_refs = set()

    # Read env files
    for env_name in [".env", ".env.local", ".env.example", ".env.production", ".env.development"]:
        env_path = root / env_name
        if env_path.exists():
            content = read_file_safe(env_path)
            vars_in_file = re.findall(r'^([A-Z][A-Z0-9_]+)=', content, re.MULTILINE)
            env_files[env_name] = vars_in_file

    # Scan code for env references (simplified — scan common directories)
    scan_dirs = ["src", "app", "pages", "lib", "utils", "components", "server"]
    scan_extensions = {".ts", ".tsx", ".js", ".jsx", ".mjs"}
    
    for scan_dir in scan_dirs:
        dir_path = root / scan_dir
        if not dir_path.exists():
            continue
        for file_path in dir_path.rglob("*"):
            if file_path.suffix in scan_extensions:
                content = read_file_safe(file_path)
                # process.env.VARIABLE
                code_refs.update(re.findall(r'process\.env\.([A-Z][A-Z0-9_]+)', content))
                # import.meta.env.VARIABLE
                code_refs.update(re.findall(r'import\.meta\.env\.([A-Z][A-Z0-9_]+)', content))

    # Find all defined vars across all env files
    all_defined = set()
    for vars_list in env_files.values():
        all_defined.update(vars_list)

    # Find missing: referenced in code but not in any env file
    missing = sorted(code_refs - all_defined)

    return {
        "env_files": env_files,
        "code_references": sorted(code_refs),
        "defined": sorted(all_defined),
        "missing_in_env": missing,
    }


def main():
    project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    
    if not project_root.exists():
        print(f"Error: Directory not found: {project_root}", file=sys.stderr)
        sys.exit(1)

    pkg_path = project_root / "package.json"
    if not pkg_path.exists():
        print(f"Error: No package.json found in {project_root}", file=sys.stderr)
        sys.exit(1)

    pkg = json.loads(read_file_safe(pkg_path))
    env_data = collect_env_vars(project_root)
    all_env_vars = env_data["code_references"]

    report = {
        "project_root": str(project_root),
        "project_name": pkg.get("name", "unknown"),
        "package_manager": detect_package_manager(project_root),
        "framework": detect_framework(project_root, pkg),
        "database": detect_database(project_root, pkg, all_env_vars),
        "auth": detect_auth(project_root, pkg, all_env_vars),
        "payments": detect_payments(project_root, pkg, all_env_vars),
        "deploy_config": detect_deploy_config(project_root),
        "environment_variables": env_data,
        "build_command": pkg.get("scripts", {}).get("build", "npm run build"),
        "start_command": pkg.get("scripts", {}).get("start", "npm start"),
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
