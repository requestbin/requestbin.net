from requestbin import config
import os

from requestbin import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', config.PORT_NUMBER))
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG)