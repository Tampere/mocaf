import React, { useEffect, useState } from 'react';
import Papa from 'papaparse';
import 'mapbox-gl/dist/mapbox-gl.css';
import { gql, useQuery } from "@apollo/client";

import {Client as Styletron} from 'styletron-engine-atomic';
import {Provider as StyletronProvider} from 'styletron-react';
import {LightTheme, BaseProvider} from 'baseui';
import {StyledSpinnerNext as Spinner} from 'baseui/spinner';

import i18n from './common/i18n';
import { TransportModeShareMap } from './Map';
import Controls from './Controls';
import { useAnalyticsData } from './data';


const engine = new Styletron();


const GET_AREAS = gql`
  query getAreas {
    analytics {
      areaTypes {
        id
        topojsonUrl
        dailyTripsUrl
        dailyLengthsUrl
        areas {
          id
          identifier
          name
        }
      }
    }
    transportModes {
      id
      identifier
      name
    }
  }
`;

function useUserChoiceState() {
  const [weekSubset, setWeekSubset] = useState('workday');
  return {
    weekSubset: {
      value: weekSubset,
      set: setWeekSubset
    }
  };
}


export function App() {
  const { loading, error, data } = useQuery(GET_AREAS);
  const areaType = data?.analytics.areaTypes[1];
  const transportModes = data?.transportModes;
  const selectedTransportMode = transportModes?.filter((mode) => mode.identifier === 'car')[0];
  const userChoices = useUserChoiceState();

  const areaData = useAnalyticsData({
    type: 'lengths',
    weekend: false,
  });

  if (error) {
    return <div>GraphQL error: {error}</div>
  }

  let main;
  if (!loading && areaData) {
    main = (
      <TransportModeShareMap areaType={areaType} areaData={areaData} mode={selectedTransportMode} transportModes={transportModes} />
    );
  } else {
    main = <Spinner />;
  }

  return (
    <StyletronProvider value={engine}>
      <BaseProvider theme={LightTheme}>
        <div style={{display: 'flex', height: '100vh'}}>
          <div style={{width: '280px', height: '100vh'}}>
            <Controls userChoices={userChoices} />
          </div>
          <div style={{width: 'calc(100vw - 280px)', height: '100vh'}}>
            {main}
          </div>
        </div>
      </BaseProvider>
    </StyletronProvider>
  );
}
