import * as R from "ramda"

import "./Parameters.css"

export default function Parameters({settings, onChangeSettings}) {
  const { starTime, toTime, fromTime, Fr, N, W, DA, DP } = settings
  return (
    <div className="settings-container">
      <div>
        <label>
          STARTIME <input type="number" value={starTime} onChange={e => onChangeSettings(R.assoc('starTime', e.target.valueAsNumber))}/>
        </label>
        <label>
          TOTIME <input type="number" value={toTime} onChange={e => onChangeSettings(R.assoc('toTime', e.target.valueAsNumber))}/>
        </label>
        <label>
          FROMTIME <input type="number" value={fromTime} onChange={e => onChangeSettings(R.assoc('fromTime', e.target.valueAsNumber))}/>
        </label>
      </div>

      <div>
        <label>
          Fr <input type="number" value={Fr} onChange={e => onChangeSettings(R.assoc('Fr', e.target.valueAsNumber))}/>
        </label>
        <label>
          N <input type="number" value={N} onChange={e => onChangeSettings(R.assoc('N', e.target.valueAsNumber))}/>
        </label>
        <label>
          W <input type="number" value={W} onChange={e => onChangeSettings(R.assoc('W', e.target.valueAsNumber))}/>
        </label>
        <label>
          DA <input type="number" value={DA} onChange={e => onChangeSettings(R.assoc('DA', e.target.valueAsNumber))}/>
        </label>
        <label>
          DP <input type="number" value={DP} onChange={e => onChangeSettings(R.assoc('DP', e.target.valueAsNumber))}/>
        </label>
      </div>
    </div>
  )
}
