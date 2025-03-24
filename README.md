Some notes for myself on how this blog is setup. 

## Static Content Generation


## Publishing

The site is hosted with [Github Pages](https://pages.github.com) which means that the site is contained in the `gh-pages` branch of the repository. 

### Github Actions

The new way to publish is with Github Actions ([docs](https://gohugo.io/hosting-and-deployment/hosting-on-github/)).                         

### `publish_to_ghpages` script

The old way to do this was through the steps of checking out the `gh-pages` branch; creating the site; committing everything in `public` and pushing. There is a helper script `publish_to_ghpages.sh` that automates these steps.  