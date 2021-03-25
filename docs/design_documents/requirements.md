---
layout: page
title: Requirements
permalink: /requirements/
parent: Design Documents
nav_order: 3
---

## Requirements

If you have feedback, please [Suggest or prioritize a Requirement](https://docs.google.com/forms/d/e/1FAIpQLScg34b0NJhuDWaUUvyWJxyK5bBGf9Hh9N0n76XElsoBJd7S1Q/viewform?usp=sf_link) by April 25th!

### Must Have

<table>
  {% for row in site.data.must_have %}
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

### Should Have

<table>
  {% for row in site.data.should_have %}
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

### Could Have

<table>
  {% for row in site.data.could_have %}
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

### Won't Have

<table>
  {% for row in site.data.wont_have %}
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