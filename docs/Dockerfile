FROM jekyll/jekyll:4
MAINTAINER Gregory Wiedeman gwiedeman@albany.edu

ENV TZ=America/New_York
ENV JEKYLL_ENV=production

EXPOSE 4000

WORKDIR /code

COPY Gemfile* ./

RUN bundle install

COPY . /code

ENTRYPOINT ["jekyll serve --force_polling --verbose --livereload"]