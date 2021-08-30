---
layout: page
title: User Stories
permalink: /user_stories/
parent: Design Documents
nav_order: 2
---

# User Stories

If you have feedback, please [Suggest a User Story](https://docs.google.com/forms/d/e/1FAIpQLSf68TbV5mbZ48pm_lrGB_SK4oxZO0FtGeUqOfoK6gEQ5iq2WA/viewform?usp=sf_link) by April 25th!

<table>
  {% for row in site.data.user_stories %}
    {% if forloop.first %}
    <tr>
      {% for pair in row %}
        <th>{{ pair[0] }}</th>
      {% endfor %}
    </tr>
    {% endif %}
    {% tablerow pair in row %}
      {{ pair[1] }}
    {% endtablerow %}
  {% endfor %}
</table>