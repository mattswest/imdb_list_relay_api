#!/usr/bin/env bash
# Install a sudoers rule that lets user 'matt' restart the IMDb relay
# service without being prompted for a password.
#
# Usage: sudo ./install-sudoers.sh

set -euo pipefail

# Every value is hardcoded on purpose. This installer runs as root and
# persists a NOPASSWD rule, so neither the grantee, the unit, nor the
# destination may be chosen by the caller.
SERVICE_USER="matt"
UNIT="imdb-relay.service"
SUDOERS_FILE="/etc/sudoers.d/imdb-relay-restart"

UNIT_SHORT="${UNIT%.service}"
PROGRAM_NAME="$(basename "$0")"

die() {
    printf '%s: error: %s\n' "$PROGRAM_NAME" "$*" >&2
    exit 1
}

[ "$(id -u)" -eq 0 ] || die "must run as root; try: sudo $0"

# PATH is caller-controlled even under root, and the resolved path is
# persisted verbatim into a NOPASSWD rule. Accept only known absolute
# locations that are root-owned and not writable by group or others.
resolve_trusted() {
    local name="$1"
    shift
    local candidate
    for candidate in "$@"; do
        [ -x "$candidate" ] || continue
        [ "$(stat -Lc '%u' "$candidate")" -eq 0 ] || die "$candidate is not owned by root"
        [ -z "$(find -L "$candidate" -maxdepth 0 -perm /022 -print -quit)" ] ||
            die "$candidate is group- or world-writable"
        printf '%s\n' "$candidate"
        return 0
    done
    die "no trusted $name binary found (looked in: $*)"
}

systemctl_path="$(resolve_trusted systemctl /usr/bin/systemctl /bin/systemctl)"
visudo_path="$(resolve_trusted visudo /usr/sbin/visudo /sbin/visudo)"

id -u "$SERVICE_USER" >/dev/null 2>&1 || die "no such user: $SERVICE_USER"
"$systemctl_path" cat "$UNIT" >/dev/null 2>&1 || die "no such systemd unit: $UNIT"

staged_file="$(mktemp)"
trap 'rm -f "$staged_file"' EXIT

# sudo matches the command line literally, so "restart imdb-relay" and
# "restart imdb-relay.service" are distinct rules. Grant both spellings and
# nothing else: no wildcards, no blanket systemctl access.
cat >"$staged_file" <<EOF
# Managed by $PROGRAM_NAME - passwordless restart of $UNIT.
$SERVICE_USER ALL=(root) NOPASSWD: $systemctl_path restart $UNIT_SHORT, $systemctl_path restart $UNIT
EOF

chmod 0440 "$staged_file"
"$visudo_path" -c -q -f "$staged_file" || die "generated rule failed syntax validation; nothing installed"

install -o root -g root -m 0440 "$staged_file" "$SUDOERS_FILE"
"$visudo_path" -c -q -f "$SUDOERS_FILE" || die "installed rule failed syntax validation: $SUDOERS_FILE"

printf 'installed %s\n' "$SUDOERS_FILE"
printf 'granted to %s:\n' "$SERVICE_USER"
sed -n '2p' "$SUDOERS_FILE"
printf '\nverify as %s with:\n  sudo -n systemctl restart %s\n' "$SERVICE_USER" "$UNIT_SHORT"
