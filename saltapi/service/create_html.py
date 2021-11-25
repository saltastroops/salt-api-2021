import webbrowser
from typing import Dict, List, Any

from saltapi.web.schema.common import Semester, ProposalCode


def create_html(
        proposal_code: ProposalCode,
        semester: Semester,
        previous_requests: List[Dict[str, Any]],
        previous_conditions: Dict[str, Any],
        new_request: Dict[str, any]
):
    html_content = '''
<!DOCTYPE html>
<html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Title</title>
    </head>
    <style>
      body{
        margin: 2em 4em 3em;
        line-height: 1.5;
      }
      table, th {
        border:1px solid black;
      }
      table {
        width: 100%;
        border-collapse: collapse;
      }
      td {
        padding-left: 10px;
        border-right:1px solid black;
      }
      .section {
        border:1px solid black;
        padding: 1.5em;
        margin-bottom: 2em;
      }
      .upper-margin{
        border-top:1px solid black;
      }
      hr {
        margin-right: -1.5em;
        margin-left: -1.5em;
      }
      table, tr, td, th, tbody, thead, tfoot, .section {
        page-break-inside: avoid !important;
      }
      .has-two-columns {
        display: grid;
        grid-template-columns: 200px 1fr;
      }
      .left-shifted {
        margin-left: 1em;
      }
      .numbering {
        display: grid;
        grid-template-columns: 25px 1fr;
      }
    </style>
    <body>
        <div>
            <h2>
                Multisemester Proposal Progress Report: 
            </h2>
    '''
    html_content += f'''
            <h2>
                {proposal_code} -- TODO -- (Oppor)
            </h2>
            <div class="section"><div>This report is for semester {semester}</div></div>
            <div class="section">
                <div class="numbering">
                    <div><h3>1.</h3></div>
                    <div><h3>PREVIOUS REQUESTS, ALLOCATIONS, COMPLETENESS</h3></div>
                    <div></div>
                    <div>
                      <i>
                        This section lists the originally requested times, as well as the allocated times and the completion. It also gives the originally requested observing conditions.
                      </i>
                    </div>
                </div>
                <hr>
                <div>
                    <h4>Original time requests, time allocations and completeness</h4>
                    <table>
                      <tr>
                        <th>Semester</th>
                        <th>Requested Time</th>
                        <th>Allocated Time</th>
                        <th>Observed Time</th>
                        <th>Completion</th>
                      </tr>
'''
    for p in sorted(previous_requests, key = lambda i: i['semester']):
        html_content += f'''
                      <tr>
                        <td>{p['semester']}</td>
                        <td>{p['requested']} seconds</td> 
                        <td>{p['allocated']} seconds</td> 
                        <td>{p['observed']} seconds</td> 
                        <td>{round((p['observed']/p['allocated'])*100, 1)} %</td>
                      </tr>
        '''
    html_content += f'''
                    </table>
                    <h4>Previously requested observing conditions</h4>
                    <div>
                        <div class="has-two-columns">
                            <div class="left"><b>Maximum seeing:</b></div>
                            <div class="right">{previous_conditions['seeing']} arcseconds</div>
                        </div>
                        <div class="has-two-columns">
                            <div class="left"><b>Transparency:</b></div>
                            <div class="right">{previous_conditions['transparency']}</div>
                        </div>    
                        <div>
                            <b>Brief description of observing conditions:</b>
                        </div>
                        <div>
                            <div class="left-shifted">{previous_conditions['description']}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="section">
                <div class="numbering">
                    <div><h3>2.</h3></div>
                    <div><h3> REQUEST FOR THE NEXT SEMESTER</h3></div>
                    <div></div>
                    <div><i>This section lists the requests for the next semester.</i></div>
                </div>
                <hr>
                <div>
                    <h4>Request for semester {new_request['semester']}</h4>
                    <div>
                        <div class="has-two-columns">
                            <div class="left"><b>Requested time:</b></div>
                            <div class="right">{new_request['requested_time']} seconds</div>
                        </div>
                        <div class="has-two-columns">
                            <div class="left"><b>Maximum seeing:</b></div>
                            <div class="right">{new_request['seeing']} arcseconds</div>
                        </div>
                        <div class="has-two-columns">
                            <div class="left"><b>Transparency:</b></div>
                            <div class="right">{new_request['transparency']}</div>
                        </div>
                        <div><b>Brief description of observing conditions:</b></div>
                        <div>
                            <div class="left-shifted">{new_request['description']}</div>
                        </div>
                    </div>
                    <br>
                    <div><b>The following reasons are given for changes from the original requests.</b></div>
                    <div class="left-shifted">Please see the attached document. -- TODO Double Check this content --</div>
                    <br>
                    <div><b>A supplementary pdf is attached to this report -- TODO: this needs to be a boolean to show --</b></div>
                </div>
            </div>
            <div class="section">
                <div class="numbering">
                    <div><h3>3.</h3></div>
                    <div><h3>STATUS SUMMARY</h3></div>
                    <div></div>
                    <div><i>This section gives a summary of the proposal status.</i></div>
                </div>
                <hr>
                <div>
                    <p>Please see the attached document.-- TODO Double Check this content --</p>
                </div>
            </div>
            <div class="section">
                <div class="numbering">
                    <div><h3>4.</h3></div>
                    <div><h3>STRATEGY CHANGES</h3></div>
                    <div></div>
                    <div><i>This section outlines how the TAC suggestions regarding a change of strategy will be addressed.</i></div>
                </div>
                <hr>
                <div>
                    <p>Please see the attached document.-- TODO Double Check this content --</p>
                </div>
            </div>
        </div>

        <div>
            <div class="section">
                <b>Reasons why the time request has changed</b>
                <p>{new_request['change_reason']}</p>
            </div>
            <div class="section">
                <b>Summary of your proposal's status</b>
                <p>{new_request['status_summary']}</p>
            </div>
            <div class="section">
                <b>Strategy changes</b>
                <p>{new_request['change_strategy']}</p>
            </div>
        </div>
    </body>
</html>  
    '''

    with open('./pdf_report.html', 'w') as f:
        f.write(html_content)


    imaginary_prev = [
        {
            "semester": "2020-1",
            "requested": 119000,
            "allocated": 101150,
            "observed": 14346
        },
        {
            "semester": "2020-2",
            "requested": 119000,
            "allocated": 101150,
            "observed": 14346
        },
        {
            "semester": "2021-1",
            "requested": 119000,
            "allocated": 101150,
            "observed": 14346
        }
    ]
    imaginary_next = {
        "semester": '2021-2',
        "requested_time": 119000,
        "seeing": 1,
        "transparency": "Thin clouds",
        "description": "1\" slit required for spectral resolution, despite the seeing constraint of 2.5\""
    }
