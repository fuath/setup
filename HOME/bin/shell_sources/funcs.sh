printv() {  # v for verbatim
    printf '%q\n' "$1"
}

# 'less' using vim
vless() {
    # http://vimdoc.sourceforge.net/htmldoc/starting.html#$VIMRUNTIME
    # http://vimdoc.sourceforge.net/htmldoc/various.html#less
    # maybe use https://github.com/rkitover/vimpager instead?
    local vimruntime=`vim -e -T dumb --cmd 'exe "set t_cm=\<C-M>"|echo $VIMRUNTIME|quit' | tr -d '\015' `
    local lessvim="$vimruntime/macros/less.vim"
    vim -u "$lessvim" "$@"
}

# mkdir + cd
mcd() {
    if [[ -z "$1" ]]; then
        ercho "missing argument"
        return 1
    fi
    mkdir -p "$1" && cd "$1";
}

# cd + ls
cl() {
    cd "$1" && ls "${@:2}"
}

# download
dl() {
    if [[ -n "$1" ]] && [[ ! $1 == -* ]]; then
        # an argument provided that doesn't start with dash
        local url="$1"; shift
    else
        local url="$(cb)"  # get from clipboard
    fi

    echo "${COLOR_BOLD}${COLOR_BLUE}Downloading: ${COLOR_YELLOW}$url${COLOR_RESET}"

    if [[ $url == magnet:* ]] || [[ $url == *.torrent ]]; then
        aria2c "$@" "$url"
    else
        youtube-dl "$@" "$url"
    fi
}

# get the homedir of another user. Be careful cause of eval.
# http://stackoverflow.com/a/20506895
user_home() {
    eval echo "~$1"
}

my_home() {
    user_home $(logname)
}

filter() {
    # take a space-separated string of words and filter it
    # based on a filter expression (like "word" or "word1|word2").
    # This seems goofy but at least it's a simple one-liner.
    echo $1 | tr ' ' '\n' | egrep -wv "$2" | tr '\n' ' '
}

is_remote() {
    [[ $SSH_TTY || $SSH_CLIENT ]]
}

is_su() {
    [[ $USER != "$(logname)" ]]  # if current user != login user
}

is_root() {
    [[ $EUID == 0 ]]
}
