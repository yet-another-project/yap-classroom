**Attention:** The tool specified below does a two-way sync, therefore you could
lose email on the gmail servers if you delete them locally. Please take care!

OfflineIMAP
===========
In order to actually have something to work with we need to download all the emails
sent to our mailing list. We do this by using the `offlineimap` tool and
downloading every email received by us that has a specific label in the gmail
web interface, in this case all yet-another-project emails have been labeled
with `yap/phpro-book`.

Install `offlineimap` and:

1. Create a configuration file in `~/.offlineimaprc`, an example can be found in
`offlineimaprc-example` in this directory.

2. Create your `localfolders` directory.

3. Run `offlineimap`

Email-analysis
==============
Processing and analysing the emails:

1. Copy `config.ini-example` to `config.ini` and modify the paths according to
your setup.
 * `cachefile` should point to an inexistent file (will be created) or to an
  existent cache file created by previous runs of this project
 * `maildir` is the Maildir directory created by `offlineimap` above and should
  contain the `cur`, `new` and `tmp` directories specific for the Maildir
  structure, make sure that the directory `cur` contains some emails to be
  parsed

2. Run `./main.py`
