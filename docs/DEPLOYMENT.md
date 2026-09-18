# Running and operating Green Thumb

## Local use

The [README](../README.md) gives the quick start. The base install supports dictionary browsing and feedback. Classification additionally needs the ML dependencies and a trusted `model.h5`.

`python app.py` listens on `127.0.0.1:5000` with debugging disabled. The Flask CLI can also load the factory: `flask --app app:create_app run`.

## Server process

Use a WSGI server when preparing a deployment:

```bash
waitress-serve --host=127.0.0.1 --port=8000 --call app:create_app
```

Waitress is supported on Windows and Unix; see the [official Flask deployment guidance](https://flask.palletsprojects.com/en/stable/deploying/waitress/). This command listens on loopback for use behind a reverse proxy. It does not publish the app to the internet.

For a hosted service:

1. Configure a persistent random `SECRET_KEY`, even if admin access is disabled. Otherwise each process generates its own ephemeral session key.
2. Terminate HTTPS at a configured reverse proxy and set `COOKIE_SECURE=1`. Browsers require a secure context for remote camera access.
3. Configure the proxy's upload/body/time limits consistently with the application; the application caps requests at 8 MiB.
4. Keep `instance/` on a writable persistent volume and back up `feedback.sqlite3`. Establish retention/deletion procedures. The current administration view returns the latest 100 submissions, not a complete data-management console.
5. Install and configure shared rate-limit storage for multiple processes, for example `pip install 'limits[redis]'` and set `RATELIMIT_STORAGE_URI` to your managed Redis URL. The default memory store resets on restart and does not coordinate across processes.
6. Configure trusted proxy handling for your actual topology before relying on per-client IP rate limiting. The app deliberately does not trust arbitrary forwarded headers; behind an unconfigured proxy, all visitors may share its rate limit.
7. Mount the model read-only, verify its checksum and test inference on the intended machine. Model files must come from a trusted source. Each process holds a separate model copy; concurrent predictions within a process are serialized.
8. Measure throughput, memory and latency before choosing worker/thread counts. Put a queue or stricter admission controls in front of inference if traffic warrants it.
9. Monitor failures and protect logs. Test backup restoration, session behavior and camera access before sharing the URL.

`GET /health` is a process liveness check; it intentionally does not assert model readiness, database writeability or inference accuracy.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Random per process | Session and CSRF signing; persist for hosted use |
| `ADMIN_USERNAME` | `admin` | Admin account name |
| `ADMIN_PASSWORD_HASH` | Empty (login disabled) | Werkzeug password hash, never the plaintext password |
| `MODEL_PATH` | Root `model.h5` | Absolute paths recommended for deployment |
| `COOKIE_SECURE` | `0` | Set `1` with HTTPS |
| `RATELIMIT_STORAGE_URI` | `memory://` | Shared storage URL for multi-process deployments |

`.env.example` is documentation. The app does not automatically read `.env` files. Set variables in your shell, service manager or deployment platform.

## Data handling

Images are decoded and classified in memory. Feedback stores an issue, description and UTC timestamp in SQLite. Administrators can read the latest submissions. The application does not request email addresses or persist uploaded images. Review deployment-layer logging separately.

The historical `feedback.json` is deliberately retained locally and excluded from Git. New installations begin with an empty database; no historic feedback is silently republished or migrated.
