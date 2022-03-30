set -U fish_term24bit 1
set -U fish_color_search_match 'fff'
set -U fish_color_error 'f99'
set -U fish_color_autosuggestion '999'
set -U fish_color_valid_path  # Remove underlines on paths
set -U fish_color_command '39d'

function fish_prompt

  if [ $SERVER_ENV = 'development' ]
    set_color -b '00a600'
    set_color '000'
  else if [ $SERVER_ENV = 'staging' ]
    set_color -b 'd8b500'
    set_color '000'
  else if [ $SERVER_ENV = 'production' ]
    set_color -b 'e60000'
    set_color 'fff'
  else
    set_color -b 999
  end

  printf ' '
  printf $SERVER_ENV
  printf ' '

  set_color -b normal
  set_color yellow
  printf ' ➜ '
  set_color cyan
  printf (basename $PWD)
  printf ' 🐟 '
  set_color normal
end


function npmbuild
    cd /usr/srv/app/assets/
    npm i
    npm run build
    cd /usr/srv/app/
    manpy collectstatic --no-input
end


function fish_greeting
    echo ""
    echo "🐟 Installed aliases..."
    echo "sp - Runs python manage.py shell_plus"
    echo "manpy - Shorthand for python manage.py"
    echo ""
end


alias sp="/usr/local/bin/poetry run python manage.py shell_plus"

alias serveup="/usr/local/bin/poetry run uwsgi --ini /etc/uwsgi.ini"
alias servedown="/usr/local/bin/poetry run uwsgi --stop /tmp/uwsgi-master.pid"
alias servenew="touch /tmp/uwsgi-master.pid"
alias servetop="/usr/local/bin/poetry run uwsgitop /tmp/uwsgistats.sock"
alias manpy="/usr/local/bin/poetry run python manage.py"
alias failstate="fail2ban-client status | sed -n 's/,//g;s/.*Jail list://p' | xargs -n1 fail2ban-client status"
alias fishconf="nano ~/.config/fish/config.fish"

alias octal="stat -c '%a'"

eval (envkey-source)
# source $HOME/.poetry/env


# If there's an activate.fish file, then source it
if [ -e ".venv/bin/activate.fish" ]
    source .venv/bin/activate.fish
end


cd /srv/www/openownership.org/app/ && source .venv/bin/activate.fish
