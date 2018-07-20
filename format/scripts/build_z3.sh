#! /bin/bash

default_repo="https://github.com/Z3Prover/z3"
default_branch="master"

sync_repo="https://github.com/LChernigovskaya/spacer"
sync_branch="sync"

repo="$default_repo"
branch="$default_branch"

function print_help {
  echo "options:"
  echo "  -h --help    displays this message"
  echo "  -f --force   forces to re-clone and re-build z3"
  # echo "  -s --sync    use clause synchronization"
  # echo "               => build      $sync_repo ($sync_branch branch)"
  # echo "                  instead of $default_repo"
}

function build_sync {
  repo="$sync_repo"
  branch="$sync_branch"
}

while [[ $# -gt 0 ]] ; do
  case "$1" in
    -h|--help)
      print_help
      exit 0
      ;;
    -f|--force)
      rm -rf z3
      rm -rf src/*z3*
      ;;
    # -s|--sync)
    #   build_sync
    #   ;;
    *)
      echo "unexpected argument '$1'"
      echo
      print_help
      exit 2
      ;;
  esac
  shift
done


build_sync



if [ -d src/z3 ] ; then
  exit 0
fi

if [ ! -d z3 ] ; then
  echo "|===| Cloning $repo"
  echo
  echo
  git clone "$repo" z3
  echo
  echo
fi

if [ ! -d z3/build ] ; then
  cd z3
  git checkout "$branch"
  python scripts/mk_make.py --python
  cd build ; make -j 4
  cd ../..
fi

for file in `find z3/build/ -iname "libz3.*"` ; do
  cp "$file" .
done
for file in `find z3/build/ -iname "*.py"` ; do
  cp "$file" src/.
done
