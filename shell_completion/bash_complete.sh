_globus_completion() {
    local IFS=$'\t'
    if type globus > /dev/null;
    then
        COMPREPLY=( $( env COMP_LINE="$COMP_LINE" COMP_POINT="$COMP_POINT" \
                       globus --shell-complete BASH ) )
    else
        COMPREPLY=( )
    fi
    return 0
}

complete -F _globus_completion -o nospace globus;
