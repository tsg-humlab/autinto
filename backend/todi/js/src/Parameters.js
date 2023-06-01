import * as R from "ramda"

import "./Parameters.css"

export default function Parameters({settings, onChangeSettings}) {
  const { starTime, toTime, fromTime, Fr, N, W, DA, DP } = settings
  return (
    <div className="settings-container">
      <div>
        <label>
          STARTIME <input value={starTime} onChange={e => onChangeSettings(R.assoc('starTime', e.target.value))}/>
        </label>
        <label>
          TOTIME <input value={toTime} onChange={e => onChangeSettings(R.assoc('toTime', e.target.value))}/>
        </label>
        <label>
          FROMTIME <input value={fromTime} onChange={e => onChangeSettings(R.assoc('fromTime', e.target.value))}/>
        </label>
      </div>

      <div>
        <label>
          Fr <input value={Fr} onChange={e => onChangeSettings(R.assoc('Fr', e.target.value))}/>
        </label>
        <label>
          N <input value={N} onChange={e => onChangeSettings(R.assoc('N', e.target.value))}/>
        </label>
        <label>
          W <input value={W} onChange={e => onChangeSettings(R.assoc('W', e.target.value))}/>
        </label>
        <label>
          DA <input value={DA} onChange={e => onChangeSettings(R.assoc('DA', e.target.value))}/>
        </label>
        <label>
          DP <input value={DP} onChange={e => onChangeSettings(R.assoc('DP', e.target.value))}/>
        </label>
      </div>
    </div>
  )
}
