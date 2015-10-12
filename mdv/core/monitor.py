import os
import sys
import time

from .helpers import j
from .printers import col


# Following just file monitors, not really core feature so the prettyfier:
# but sometimes good to have at hand:
# ---------------------------------------------------------------- File Monitor


def monitor(args):
    """ file monitor mode """
    if not args.filename:
        print(col('Need file argument', 2))
        raise SystemExit
    last_err = ''
    last_stat = 0
    while True:
        if not os.path.exists(args.filename):
            last_err = 'File %s not found. Will continue trying.' \
                       % args.filename
        else:
            try:
                stat = os.stat(args.filename)[8]
                if stat != last_stat:
                    last_stat = stat
                last_err = ''
            except Exception as ex:
                last_err = str(ex)
        if last_err:
            print('Error: %s' % last_err)
        sleep()


def sleep():
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print('Have a nice day!')
        raise SystemExit

# ----------------------------------------------------------- Directory Monitor


def run_changed_file_cmd(cmd, fp, pretty, colors):
    """ running commands on changes.
        pretty the parsed file
    """

    dir_mon_filepath_ph = '_fp_'
    dir_mon_content_raw = '_raw_'
    dir_mon_content_pretty = '_pretty_'

    with open(fp) as f:
        raw = f.read()
    # go sure regarding quotes:
    for ph in (dir_mon_filepath_ph, dir_mon_content_raw,
               dir_mon_content_pretty):
        if ph in cmd and not ('"%s"' % ph) in cmd \
                        and not ("'%s'" % ph) in cmd:
            cmd = cmd.replace(ph, '"%s"' % ph)

    cmd = cmd.replace(dir_mon_filepath_ph, fp)
    print(col('Running %s' % cmd, colors['H1']))
    for r, what in ((dir_mon_content_raw, raw),
                    (dir_mon_content_pretty, pretty)):
        cmd = cmd.replace(r, what.encode('base64'))

    # yeah, i know, sub bla bla...
    if os.system(cmd):
        print(col('(the command failed)', colors['R']))


def monitor_dir(args, colors, mon_max_files):
    """ displaying the changed files """

    def show_fp(fp):
        args['MDFILE'] = fp
        print("(%s)" % col(fp, colors['L']))
        cmd = args.get('change_cmd')
        if cmd:
            run_changed_file_cmd(cmd, fp=fp, pretty=pretty)

    ftree = {}
    d = args.get('-M')
    # was a change command given?
    d += '::'
    d, args['change_cmd'] = d.split('::')[:2]
    args.pop('-M')
    # collides:
    args.pop('-m')
    d, exts = (d + ':md,mdown,markdown').split(':')[:2]
    exts = exts.split(',')
    if not os.path.exists(d):
        print(col('Does not exist: %s' % d, colors['R']))
        sys.exit(2)

    dir_black_list = ['.', '..']

    def check_dir(d, ftree):
        check_latest = ftree.get('latest_ts')
        d = os.path.abspath(d)
        if d in dir_black_list:
            return

        if len(ftree) > mon_max_files:
            # too deep:
            print(col('Max files (%s) reached' % col(mon_max_files, colors['R'])))
            dir_black_list.append(d)
            return
        try:
            files = os.listdir(d)
        except Exception as ex:
            print('%s when scanning dir %s' % (col(ex, colors['R']), d))
            dir_black_list.append(d)
            return

        for f in files:
            fp = j(d, f)
            if os.path.isfile(fp):
                f_ext = f.rsplit('.', 1)[-1]
                if f_ext == f:
                    f_ext == ''
                if f_ext not in exts:
                    continue
                old = ftree.get(fp)
                # size:
                now = os.stat(fp)[6]
                if check_latest:
                    if os.stat(fp)[7] > ftree['latest_ts']:
                        ftree['latest'] = fp
                        ftree['latest_ts'] = os.stat(fp)[8]
                if now == old:
                    continue
                # change:
                ftree[fp] = now
                if not old:
                    # At first time we don't display ALL the files...:
                    continue
                # no binary. make sure:
                if 'text' in os.popen('file "%s"' % fp).read():
                    show_fp(fp)
            elif os.path.isdir(fp):
                check_dir(j(d, fp), ftree)

    ftree['latest_ts'] = 1
    while True:
        check_dir(d, ftree)
        if 'latest_ts' in ftree:
            ftree.pop('latest_ts')
            fp = ftree.get('latest')
            if fp:
                show_fp(fp)
            else:
                print('sth went wrong, no file found')
        sleep()
